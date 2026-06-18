# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/hrt/stream2mmio_defs.h

Purpose: defines Stream2MMIO register indices and command/ack/packer token layouts.

Important APIs/types/functions: macros cover register alignment, per-SID command/ack/pixel-width/address/stride/count/block registers, SID register spacing, maximum SID count, command token field positions and values, pack acknowledgement item/EOP/EOF/valid bits, ACK token layout, and packer commands for words/long packets/short packets.

Control flow: no direct flow. Stream2MMIO host helpers use these constants for MMIO access and command interpretation.

State and persistence: no software state; constants describe hardware register/token ABI.

Dependencies and integration: includes `mipi_backend_defs.h` because Stream2MMIO consumes MIPI backend stream output.

Risks and test signals: header guard name contains `MMMIO`, but it is self-consistent. Tests should validate command token generation, acknowledgement parsing, and register bank stride for multiple SIDs.
