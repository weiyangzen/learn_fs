# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_of_hw_prober.c

Purpose: OF/DT hardware prober for ChromeOS devices with drop-in I2C component variants, such as alternate touchscreens or trackpads.

Important APIs, types, and functions: `struct hw_prober_entry` maps a machine compatible to a prober function and data. `struct chromeos_i2c_probe_data` wraps I2C OF prober config and simple options. `chromeos_i2c_component_prober()` calls `i2c_of_probe_component()`. Static data describes dumb and simple probing for touchscreen/trackpad types, with board-specific power/reset delays for Hana and Squirtle.

Control flow: module init first checks whether any `hw_prober_platforms` entry matches `of_machine_is_compatible()`. If none match, it returns `-ENODEV`. Otherwise it registers a platform driver and a simple platform device. Probe iterates all matching entries and invokes their probers; only `-EPROBE_DEFER` stops iteration and defers probe, while other failures are ignored so later probers can run.

State and persistence: file-static `chromeos_of_hw_prober_pdev` holds the synthetic platform device until module exit. The prober mutates the live device tree through the I2C OF prober machinery, enabled by `OF_DYNAMIC`.

Dependencies and integration points: depends on OF, I2C, and the `I2C_OF_PROBER` namespace. It integrates with machine compatibles `google,hana`, `google,spherion`, `google,squirtle`, `google,steelix`, and `google,voltorb`.

Risks and edge cases: non-defer prober failures are intentionally ignored, which can hide misconfiguration. Static compatible tables must be maintained as boards/components change. Power/reset delay assumptions are encoded per board and may be sensitive to regulator or device-driver behavior.

Test signals: boot DT-based target devices and verify the chosen touchscreen/trackpad nodes become available, confirm regulator/reset sequencing on simple probes, ensure `-EPROBE_DEFER` eventually succeeds, and check module unload removes the synthetic device/driver.
