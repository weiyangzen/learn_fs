# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/Kconfig

Purpose: defines machine choices and support options for Loongson 2E/2F Lemote platforms.

Important APIs/types/functions: symbols include `LEMOTE_FULOONG2E`, `LEMOTE_MACH2F`, `CS5536`, `CS5536_MFGPT`, `LOONGSON_UART_BASE`, and `LOONGSON_MC146818`.

Control flow: under `MACH_LOONGSON2EF`, a machine choice selects either Fuloong 2E or Loongson 2F family and pulls in CPU, PCI/ISA, early printk, DMA, endian, highmem, and timer dependencies. `CS5536_MFGPT` depends on CS5536 and disables high-res timer compatibility.

State and persistence: build-time `.config` state only.

Dependencies and integration: drives Loongson2EF Makefiles, CS5536 VSM inclusion, UART/RTC support, and timer source selection.

Risks: MFGPT timer selection is incompatible with high-resolution timers and required for some CPUFreq correctness per help text.

Test signals: defconfig coverage for 2E/2F boards, Kconfig dependency resolution, and boot timer correctness.
