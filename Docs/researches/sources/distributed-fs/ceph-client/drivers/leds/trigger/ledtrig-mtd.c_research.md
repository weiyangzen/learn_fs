<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-mtd.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-mtd.c

Purpose: The MTD trigger provides activity LEDs for MTD/NAND operations.

Important APIs and state: It defines trigger pointers `ledtrig_mtd` and `ledtrig_nand`. Exported `ledtrig_mtd_activity()` blinks both triggers with fixed 30 ms on/off delays.

Control flow: `device_initcall(ledtrig_mtd_init)` registers simple triggers named `mtd` and `nand-disk`. There is no exit path for the bool trigger.

Dependencies and integration: MTD code calls the exported symbol to report activity. Kconfig depends on MTD.

Risks and test signals: Fixed one-shot blink behavior may coalesce under heavy I/O. Test trigger registration, exported call paths, and operation when no LED is attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-mtd.c -->
