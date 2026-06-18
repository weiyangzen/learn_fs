# sources/distributed-fs/ceph-client/include/soc/fsl/cpm.h

Purpose: defines common Communication Processor Module and QE parameter-RAM structures, function-code flags, command opcodes, buffer descriptors, protocol status bits, and CPM helper APIs.

Important APIs and types: `struct spi_pram` and `struct usb_ctlr` describe SPI and USB parameter RAM/register blocks. Function-code macros differ for CPM1 versus newer CPM. `cbd_t`/`struct cpm_buf_desc` is the common buffer descriptor with status/control, length, and buffer address. Many `BD_*` macros define serial, Ethernet RX/TX, transparent mode, and I2C status/control bits. `cpm_command()` is available under `CONFIG_CPM` with `-ENOSYS` fallback; `cpm2_gpiochip_add32()` registers CPM2 GPIO support.

Control flow: CPM/QE protocol drivers allocate parameter RAM and buffer descriptor rings, initialize function codes and command opcodes, submit CPM commands, and interpret descriptor ownership/error bits in interrupt or polling paths.

State and persistence: runtime state lives in CPM parameter RAM, BD rings, command engine state, GPIO registration, and DMA buffers. No persistent storage is defined.

Dependencies and integration points: includes QE definitions and kernel OF/types/errno support. Integrates serial, Ethernet, USB, SPI, I2C, and platform GPIO drivers on CPM/QE SoCs.

Risks and test signals: risks include endian/packing mistakes, descriptor ownership races, CPM1/CPM2 flag differences, command opcode aliasing, and wrong buffer address width. Test protocol TX/RX rings, error status handling, CPM disabled stubs, GPIO registration, and CPM1/CPM2/QE config builds.
