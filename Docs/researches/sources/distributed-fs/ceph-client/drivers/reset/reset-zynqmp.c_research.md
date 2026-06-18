# sources/distributed-fs/ceph-client/drivers/reset/reset-zynqmp.c

Purpose: Xilinx ZynqMP/Versal/Versal Net reset provider that forwards reset operations to platform firmware.

Important APIs/types/functions: `zynqmp_reset_soc_data` supplies base firmware reset ID and number of resets. Assert/deassert/reset call `zynqmp_pm_reset_assert()` with ASSERT, RELEASE, or PULSE. Status calls `zynqmp_pm_reset_get_status()`. `zynqmp_reset_of_xlate()` returns the one-cell reset ID.

Control flow: arch init registers the platform driver early. OF match data selects reset range; consumers pass one-cell IDs that are offset by the SoC base before firmware calls.

State and persistence: no hardware state in driver; firmware owns reset state. Software holds match data and rcdev.

Dependencies and integration: Xilinx firmware interface, OF platform probing, reset-controller framework, arch initcall ordering.

Risks and test signals: `of_xlate()` does not validate `args_count` or range itself. Firmware availability and error mapping are critical. Test invalid reset IDs, firmware unavailable/errors, each compatible reset count, and pulse/assert/release operations.
