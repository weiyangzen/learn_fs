<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genwqe/genwqe_card.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/genwqe/genwqe_card.h

## Purpose
`genwqe_card.h` exposes the userspace ABI for IBM GenWQE accelerator cards. It covers device naming, card types, MMIO register offsets, DDCB command submission, bitstream update/read operations, memory pinning, and register access ioctls.

## Important APIs, types, and functions
The header exports `GENWQE_DEVNAME`, card type IDs, unit offset helpers, SLU/SLC/HSU/APP register offsets, DDCB return codes and command options, service layer commands, `enum genwqe_card_state`, `struct genwqe_reg_io`, `struct genwqe_bitstream`, `struct genwqe_debug_data`, `struct genwqe_ddcb_cmd`, and `struct genwqe_mem`. Ioctls use `GENWQE_IOC_CODE` and include `GENWQE_READ_REG*`, `GENWQE_WRITE_REG*`, `GENWQE_GET_CARD_STATE`, `GENWQE_PIN_MEM`, `GENWQE_UNPIN_MEM`, `GENWQE_EXECUTE_DDCB`, `GENWQE_EXECUTE_RAW_DDCB`, `GENWQE_SLU_UPDATE`, and `GENWQE_SLU_READ`.

## Control flow
User space opens the GenWQE character device, optionally reads or writes diagnostic registers, pins memory for DMA reuse, prepares a DDCB command with ASIV/ASV payload and ATS fixup descriptors, then executes it synchronously. Flash and bitstream flows use the service layer update/read ioctls and service commands.

## State and persistence behavior
Persistent state may exist on the accelerator, in flash bitstreams, and in pinned user memory mappings held until unpin or file close. The card state enum describes not-available, unconfigured, configured, and failure cases. DDCB completion fields and debug data are per-command.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<linux/ioctl.h>`, and integrates with the GenWQE char driver, sysfs/debugfs naming, PCI PF/VF register windows, DMA mapping, and accelerator firmware.

## Risks and test signals
Risks include raw register access causing device recovery, stale pinned memory, ATS fixup offsets that do not match hardware expectations, struct packing changes, flash update corruption, and return-code confusion between driver errors and DDCB `retc`. Test signals include ioctl ABI size checks, DDCB echo commands, pin/unpin leak tests, PF/VF permission tests, illegal-MMIO-value handling, fault injection for DMA mapping, and flash read/update validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/genwqe/genwqe_card.h -->
