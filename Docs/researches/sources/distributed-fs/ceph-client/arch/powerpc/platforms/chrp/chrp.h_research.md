# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/chrp.h

Purpose: small internal header declaring CHRP platform helper functions shared across the CHRP source files.

Important declarations: `chrp_nvram_init`, `chrp_get_rtc_time`, `chrp_set_rtc_time`, `chrp_time_init`, and `chrp_find_bridges`.

Integration: `nvram.c` implements the NVRAM initializer; `time.c` provides RTC/time functions; `pci.c` provides bridge discovery; setup code includes these declarations to install platform machine hooks. The header relies on `struct rtc_time` being available to includers.

Risks and test signals: the file has no include guard beyond normal C compile context, so duplicate inclusion is benign only because it contains externs. Risks are prototype drift with implementing files and missing includes if function signatures change. Test signals are CHRP allmodconfig/defconfig builds and warnings-as-errors for mismatched prototypes.
