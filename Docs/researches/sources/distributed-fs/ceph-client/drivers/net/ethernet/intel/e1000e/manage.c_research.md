# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/manage.c

## Purpose

`manage.c` implements generic e1000e manageability host-interface support. It detects firmware management modes, decides whether transmit packet filtering is required for iAMT DHCP traffic, writes DHCP payloads into the host interface for firmware consumption, and decides whether management pass-through must remain enabled.

## Important APIs And Functions

`e1000_calculate_checksum` computes the 8-bit two's-complement checksum used for host-interface command headers and DHCP cookies. `e1000_mng_enable_host_if` validates that the ARC/host interface is usable by checking `hw->mac.arc_subsystem_valid`, `HICR.EN`, and previous-command completion via `HICR.C`.

Public APIs are `e1000e_check_mng_mode_generic`, `e1000e_enable_tx_pkt_filtering`, `e1000e_mng_write_dhcp_info`, and `e1000e_enable_mng_pass_thru`. Internal write helpers are `e1000_mng_write_cmd_header` and `e1000_mng_host_if_write`.

## Control Flow

Management-mode detection reads `FWSM` and compares mode bits to iAMT mode. Transmit filtering starts pessimistically enabled, disables itself if manageability is absent or the host interface cannot be read, then reads the DHCP cookie from `E1000_HOST_IF`, verifies checksum and `E1000_IAMT_SIGNATURE`, and disables filtering only when the valid cookie says firmware is not parsing DHCP traffic. Invalid cookies keep filtering enabled as the safe behavior.

DHCP write flow builds a command header with `E1000_MNG_DHCP_TX_PAYLOAD_CMD`, enables the host interface, writes payload bytes to host-interface RAM with dword alignment handling, accumulates the data sum into the header checksum, writes the header, and sets `HICR.C` to notify firmware. Pass-through detection checks `MANC.RCV_TCO_EN`; then, depending on hardware support, it consults `FWSM`/`FACTPS`, NVM management mode bits for 82574/82583, or SMBus/ASF bits to determine whether the network interface must remain available to management.

## State And Persistence Behavior

The file mutates volatile firmware interface state: `hw->mac.tx_pkt_filtering`, `hw->mng_cookie`, host-interface RAM, and `HICR.C`. It reads persistent NVM only in the 82574/82583 pass-through path via `NVM_INIT_CONTROL2_REG`; it does not modify persistent storage. Its behavior is intentionally conservative around invalid firmware cookies, preserving management filtering rather than risking DHCP frames that firmware expects to inspect.

## Dependencies And Integration Points

`manage.c` depends on `e1000.h` for register macros, host-interface structures, NVM access, management constants, and debug logging. Family-specific MAC ops provide `check_mng_mode`, and higher-level transmit paths use `hw->mac.tx_pkt_filtering` to decide whether packets need firmware-aware filtering. Power-management and close paths can use pass-through status to avoid disabling management connectivity.

## Risks

Host-interface command sequencing is timing-sensitive. If `HICR.C` never clears, commands fail after a short timeout. Length/offset validation in `e1000_mng_host_if_write` prevents overflow of management RAM; mistakes here would corrupt firmware command memory. The conservative invalid-cookie path can reduce host transmit behavior more than necessary but protects manageability. Alignment handling must preserve existing leading bytes when writes start mid-dword.

## Test Signals

Signals include correct `tx_pkt_filtering` state with manageability disabled, enabled with valid parsing cookie, disabled with valid non-parsing cookie, and enabled on invalid checksum/signature. DHCP host-interface writes should reject zero/oversized lengths, set `HICR.C`, and produce firmware-visible payloads. Pass-through should remain true for PT mode with management clock active and false when TCO receive or firmware/NVM mode requirements are absent.
