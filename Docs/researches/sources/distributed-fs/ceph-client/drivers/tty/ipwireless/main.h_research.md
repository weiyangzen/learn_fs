# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/main.h

## Purpose
`main.h` defines shared top-level IPWireless driver identity, queue sizing constants, module parameter declarations, and `struct ipw_dev`, the object connecting PCMCIA resources with the hardware, network, and tty sublayers.

## Important APIs, Types, And Functions
- `IPWIRELESS_PCCARD_NAME`, `IPWIRELESS_PCMCIA_VERSION`, and `IPWIRELESS_PCMCIA_AUTHOR` provide module/device identity.
- `IPWIRELESS_TX_QUEUE_SIZE` and `IPWIRELESS_RX_QUEUE_SIZE` define 256 KiB queue sizing constants.
- `struct ipw_dev` stores the PCMCIA link, V2/V3 flag, mapped attribute/common memory, hardware/network/tty contexts, and reboot work item.
- Externs expose global module parameters `ipwireless_debug`, `ipwireless_loopback`, and `ipwireless_out_queue`.

## Control Flow And State
This header has no executable control flow. `main.c` allocates and initializes the state it defines, then passes subordinate pointers into hardware, network, and tty creation. The `work_reboot` member is scheduled by hardware callbacks and initialized during card configuration.

## State And Persistence Behavior
`struct ipw_dev` is per-card runtime state. Mapped memory pointers must be unmapped during detach. Module parameter variables are global module state rather than per-card settings.

## Dependencies And Integration Points
It includes Linux scheduling/types, PCMCIA headers, and `hardware.h`. Forward declarations keep `ipw_network` and `ipw_tty` opaque while allowing the top-level device object to reference all sublayers.

## Risks And Edge Cases
The structure owns independently allocated objects and mapped resources, so cleanup ordering is critical. Global queue/debug/loopback settings affect every instance. `IPWIRELESS_STATE_DEBUG` can influence related compilation paths and should stay consistent with debug-state expectations.

## Test Signals
Build coverage should catch type/signature mismatches. Runtime validation is indirect: successful card probe should populate mappings and subobject pointers, and detach should leave no leaked regions, mappings, tty devices, or network associations.
