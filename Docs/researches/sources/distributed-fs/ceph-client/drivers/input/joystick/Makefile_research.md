# sources/distributed-fs/ceph-client/drivers/input/joystick/Makefile

This Makefile maps joystick Kconfig symbols to driver objects and subdirectories. It builds legacy gameport protocol drivers (`a3d.o`, `analog.o`, etc.), serial/serio drivers, parport drivers, USB/SPI/I2C drivers, and nested force-feedback support under `iforce/`.

There is no runtime control flow or state. The file is a build integration table: each `obj-$(CONFIG_...)` entry must correspond to a Kconfig symbol and source object. In this subset, `CONFIG_JOYSTICK_A3D` maps to `a3d.o` and `CONFIG_JOYSTICK_SEESAW` maps to `adafruit-seesaw.o`.

Risks are mismatched symbol names, missing objects, stale source names, and accidental omission of helper subdirectories. Test signals are kbuild coverage with joystick options as built-in and module, especially `allmodconfig`, plus verifying generated module names match Kconfig help text.
