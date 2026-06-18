# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1742.c

Purpose: supports DS1742/DS1743-style memory-mapped RTC/NVRAM devices where the RTC occupies the last 8 bytes of a larger battery-backed memory resource.

Important APIs/types/functions: `struct rtc_plat_data` holds separate NVRAM and RTC register base pointers plus `last_jiffies`. `ds1742_rtc_read_time()` and `ds1742_rtc_set_time()` implement BCD calendar access with century/control sharing. `ds1742_nvram_read()` and `ds1742_nvram_write()` expose the non-RTC portion of the resource through nvmem.

Control flow: probe maps the single memory resource, splits it into NVRAM and RTC windows using `resource_size(res) - RTC_SIZE`, starts the RTC if the stop bit is set, warns if the battery flag is absent, initializes driver data, allocates/registers the RTC, and registers nvmem. Time reads use the read latch bit and a one-jiffy delay for back-to-back reads; writes use the write bit and preserve the century bits when exiting write mode.

State and persistence: time and NVRAM persist in the mapped chip. Runtime state is just the mapped pointer split and last-read jiffies guard.

Dependencies and integration: depends on platform MMIO resources, RTC core, BCD helpers, OF matching (`maxim,ds1742`), and nvmem.

Risks and test signals: correctness depends on a resource large enough to contain both NVRAM and the trailing RTC registers. There is no alarm support. Test resource sizing, DS1742 versus DS1743 NVRAM sizes, stop-bit recovery, battery flag warning, century conversion, and nvmem reads/writes ending before the RTC window.
