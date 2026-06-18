<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/io.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/io.h

Purpose: Defines SGI SN hub I/O translation table entry helpers and I/O PRB register selection macros.

Important APIs/types/functions: `IIO_ITTE`, field shifts/masks for offset/widget/IOSP, `HUB_PIO_MAP_TO_MEM`, `HUB_PIO_MAP_TO_IO`, `IIO_ITTE_PUT`, `IIO_ITTE_DISABLE`, `IIO_ITTE_GET`, and `IIO_IOPRB(x)`.

Control flow: I/O setup writes ITTEs to map big-window PIO space to memory or widget I/O targets, disables mappings by writing an invalid widget, and locates PRB registers for widget flow-control/error management.

State and persistence: State is hardware I/O translation table entries and PRB registers in the hub. The macros write remote hub registers directly.

Dependencies and integration points: Includes SN0 hub I/O definitions and depends on `REMOTE_HUB_S/PTR` from SN address macros.

Risks: Incorrect ITTE programming can route PIO to the wrong widget or memory region. `IIO_ITTE_PUT` packs fields without runtime validation.

Test signals: PCI/Xtalk device probing, big-window PIO mapping tests, widget access, and error recovery for disabled mappings are relevant.

Source read size: 59 lines, 1868 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/io.h -->
