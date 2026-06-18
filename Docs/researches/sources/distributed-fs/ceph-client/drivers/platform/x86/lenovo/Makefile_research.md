<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Makefile

Purpose: kbuild mapping for Lenovo platform/x86 drivers, including direct object targets and a macro that prefixes several WMI/Yoga modules with `lenovo-`.

Important targets: direct targets include `ideapad-laptop.o`, `think-lmi.o`, and `thinkpad_acpi.o`. `lenovo-target-*` collects modules such as `wmi-hotkey-utilities`, `ymc`, `yogabook`, `yoga-tab2-pro-1380-fastcharger`, `wmi-camera`, `wmi-capdata`, `wmi-events`, `wmi-helpers`, `wmi-gamezone`, and `wmi-other`. `LENOVO_OBJ_TARGET` rewrites each into `lenovo-<target>.o` with a single contained object.

Control flow/build behavior: kbuild expands the macro separately for built-in and module targets using `foreach` over the basename of selected target lists.

State/persistence: no runtime state. It defines user-visible module filenames for Lenovo WMI/Yoga helper drivers.

Dependencies/integration: must stay aligned with Kconfig symbol names and source filenames in the directory.

Risks: macro indirection improves naming consistency but can obscure missing source/object mismatches. Direct targets and prefixed targets use different naming conventions intentionally.

Test signals: building selected configs should produce `ideapad-laptop` directly and `lenovo-wmi-*`/`lenovo-ymc` style prefixed modules for macro-managed targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/Makefile -->
