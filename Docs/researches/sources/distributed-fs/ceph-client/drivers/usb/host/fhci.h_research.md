# sources/distributed-fs/ceph-client/drivers/usb/host/fhci.h

## Purpose
`fhci.h` is the shared contract for the Freescale QUICC Engine FHCI driver. It defines hardware register/descriptor constants, packet and TD status encodings, controller data structures, endpoint/URB/frame state models, FIFO helpers, logging helpers, HCD conversion helpers, and cross-file function prototypes.

## Important APIs, Types, and Functions
- Hardware-facing structures: `struct fhci_pram`, `struct fhci_ep_pram`, and local register/bit definitions for USB mode, endpoint, command, event, bus mode, and packet metadata.
- Software state: `struct fhci_hcd`, `struct fhci_usb`, `struct virtual_root_hub`, `struct endpoint`, `struct ed`, `struct td`, `struct packet`, `struct urb_priv`, and `struct fhci_time_frame`.
- Enumerations: GPIO/pin indices, transfer type/mode, speed, ED state, port status, and memory allocation target.
- Helpers: `get_frame_num()`, `hcd_to_fhci()`, `fhci_to_hcd()`, logging macros, and pointer FIFO wrappers `cq_new()`, `cq_put()`, `cq_get()`, etc.

## Control Flow Role
The header does not execute control flow directly, but it defines the state machine shared by the implementation files. URBs are broken into `td` objects attached to an `ed`; TDs are scheduled into `fhci_time_frame`; frames are converted into hardware packets; completed packets set TD status; done TDs feed URB giveback. Port state transitions flow through `FHCI_PORT_POWER_OFF`, `DISABLED`, `WAITING`, `FULL`, `LOW`, and transient disconnecting states.

## State and Persistence Behavior
The header distinguishes persistent per-controller state (`fhci_hcd`, `fhci_usb`, ED/TD pools), per-endpoint state (`ed`, `endpoint`), per-URB state (`urb_priv`), and per-frame state (`fhci_time_frame`). All are volatile kernel structures. Hardware state is represented through big-endian I/O memory pointers and CPM MURAM offsets.

## Dependencies and Integration Points
Includes Linux kernel, USB HCD, kfifo, GPIO descriptor, QE, and immap headers. It is included by all FHCI implementation files and exposes prototypes for the HCD, hub, memory, queue, scheduler, TD, and optional debugfs pieces.

## Risks and Test Signals
Risks include ABI-like coupling between files, fixed pool constants (`MAX_EDS`, `MAX_TDS`), bitmask overlap mistakes, assumptions around pointer-sized kfifo entries, and legacy tasklet/API patterns. Test signals are mostly compile-time and integration-oriented: all FHCI files must agree on structure fields and prototypes; sparse/endian checking should validate I/O accesses; runtime stress should confirm ED/TD state transitions and status-bit mappings.
