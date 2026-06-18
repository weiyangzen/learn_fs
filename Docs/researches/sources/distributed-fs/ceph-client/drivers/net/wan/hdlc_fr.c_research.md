# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_fr.c

## Purpose
`hdlc_fr.c` implements Frame Relay support for generic HDLC. It configures FRAD devices, manages DLCI/PVC child netdevices, supports ANSI, CCITT, Cisco, and no-LMI modes, parses and emits LMI status traffic, and maps received Frame Relay payloads to IP, IPv6, SNAP, or Ethernet-bridged PVC devices.

## Important APIs, Types, And Functions
`struct fr_hdr` describes the Q.922 two-byte Frame Relay header. `struct pvc_device` tracks each DLCI and its optional point-to-point and Ethernet child devices. `struct frad_state` stores `fr_proto` settings, sorted PVC list, LMI timer state, DCE/DTE counters, reliability, sequence numbers, and recent error history. Core functions include `q922_to_dlci()`, `dlci_to_q922()`, `add_pvc()`, `delete_unused_pvcs()`, `fr_hard_header()`, `pvc_xmit()`, `fr_lmi_send()`, `fr_lmi_recv()`, `fr_rx()`, `fr_start()`, `fr_stop()`, `fr_add_pvc()`, `fr_del_pvc()`, and `fr_ioctl()`.

## Control Flow
`fr_ioctl()` handles protocol setup and PVC creation/deletion. Protocol setup validates LMI parameters and DCE mode, attaches NRZ/CRC16 to the hardware, allocates `frad_state` if needed, and sets `ARPHRD_FRAD`. PVC add creates either an `ARPHRD_DLCI` child named `pvc%d` or an Ethernet child named `pvceth%d`, stores it in the DLCI record, and increments DCE PVC count when a previously unused PVC becomes used. Child transmit calls `pvc_xmit()`, which verifies active state, pads Ethernet frames, ensures headroom, prepends FR encapsulation, and sends through the FRAD.

On receive, `fr_rx()` validates the Q.922 header and routes matching LMI DLCIs to `fr_lmi_recv()`. Non-LMI payloads are looked up by DLCI, FECN/BECN state is updated, and payload format is decoded: direct NLPID IP/IPv6 goes to the main PVC, SNAP OUI `00-00-00` maps to Ethertype on the main PVC, and SNAP OUI `00-80-C2` PID `00-07` maps to Ethernet frames on the Ethernet PVC. LMI timers differ by role: DTE sends status enquiries and grades reliability with N391/N392/N393, while DCE waits for requests and sends integrity or full reports.

## State And Persistence
PVCs and LMI state are in-memory only. PVC activity is a combination of administrative open count, LMI existence/new/active bits, and FRAD carrier reliability. `fr_destroy()` unregisters child devices and frees all PVC records during detach. Timers are created on protocol start and synchronously deleted on stop.

## Dependencies And Integration Points
The file integrates deeply with generic HDLC, rtnetlink netdevice registration, Ethernet setup for bridged PVCs, IPv4/IPv6/SNAP protocol demux, netdevice carrier/dormant APIs, traffic-control priority for LMI control frames, and user-space `sethdlc` ioctls. It uses child-device `ml_priv` to link back to PVC metadata.

## Risks
The PVC list is manually maintained and relies on RTNL/admin serialization. LMI parsing uses many direct byte offsets; malformed frames are checked, but any future format extension needs careful bounds auditing. `fr_lmi_send()` refuses full DCE reports that exceed `HDLC_MAX_MRU`, so very large PVC sets can fail status reporting. Active PVC state depends on timer behavior, carrier state, and DCE/DTE role, making state-machine regressions easy if changes are not tested with both roles.

## Test Signals
High-value tests attach all LMI modes, create/delete both DLCI and Ethernet PVC devices, validate netdevice type and headroom, inject malformed LMI frames, verify DTE reliability transitions after missed replies, verify DCE full-report/new-bit behavior, test IP/IPv6/SNAP receive demux, and ensure detach unregisters child devices without leaks.
