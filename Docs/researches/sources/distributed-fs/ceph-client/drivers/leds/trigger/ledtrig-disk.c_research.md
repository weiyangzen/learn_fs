<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-disk.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-disk.c

Purpose: The disk trigger exports disk activity indications through three trigger names: aggregate disk activity, disk read, and disk write.

Important APIs and state: `ledtrig_disk_activity(bool write)` is exported and blinks `disk-activity` plus either `disk-write` or `disk-read` using `led_trigger_blink_oneshot()` with a fixed 30 ms on/off delay. Trigger pointers are defined with `DEFINE_LED_TRIGGER`.

Control flow: `device_initcall(ledtrig_disk_init)` registers all three simple triggers. There is no exit path because this bool trigger is built in.

Dependencies and integration: Storage code can call the exported symbol to report read/write activity. Kconfig depends on ATA.

Risks and test signals: The fixed delay is simple but can coalesce under high I/O. Test trigger registration, exported calls before/after LED binding, and read/write-specific blink selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-disk.c -->
