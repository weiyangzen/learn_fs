# sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.h

Purpose: declares the generic SOF OF/Device Tree platform helpers and a small machine descriptor used by OF platforms.

Important APIs/types: `struct snd_sof_of_mach` carries compatible string, machine driver name, firmware filename, and topology filename. The header exports `sof_of_pm`, `sof_of_probe()`, `sof_of_remove()`, and `sof_of_shutdown()` for platform-specific drivers.

Control flow/state: no implementation state is stored here; callers provide platform devices whose match data points to `sof_dev_desc` instances consumed by `sof_of_probe()`.

Dependencies/integration: integrates OF platform drivers with the common SOF probe/remove/PM layer. It relies on the platform device and `dev_pm_ops` types being visible from including source files.

Risks/test signals: because it is a shared interface, signature changes affect all OF SOF platform drivers. Build coverage should include at least one OF SOF driver using `sof_of_pm` and the probe/remove/shutdown helpers.
