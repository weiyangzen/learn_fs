# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_init.c

Purpose: orchestrates QAT device service registration and the device up/down/restart lifecycle. It orders hardware setup, firmware load/start, interrupts, RAS, PF/VF communication, heartbeat, rate limiting, telemetry, registered services, crypto/compression algorithm registration, debugfs, and sysfs.

Important APIs: `adf_service_register`, `adf_service_unregister`, `adf_dev_up`, `adf_dev_down`, `adf_dev_restart`, `adf_dev_restarting_notify`, `adf_dev_restarted_notify`, and `adf_error_notifier`. Static phases are `adf_dev_init`, `adf_dev_start`, `adf_dev_stop`, and `adf_dev_shutdown`.

Control flow and state: `state_lock` serializes up/down. Init validates configuration, initializes ETR/admin/arbiter/AE/firmware/MSI-X/RAS/PFVF, then heartbeat/RL/TL and service `INIT`. Start sets starting/started bits, starts AE/admin/clock/PM/timer/heartbeat/RL/TL/services, registers algorithms, and adds debugfs/sysfs. Stop reverses user-facing and runtime services. Shutdown releases firmware, services, RL/RAS/heartbeat/TL/IRQs/config/admin/ETR and flushes misc work.

Dependencies and integration: central integration point for nearly every common QAT subsystem.

Risks and test signals: partial failure paths return without fully unwinding some earlier init work, relying on later down paths. Test repeated up/down/restart, failure injection at each hw callback, service unregister while active, VF auto-config, and algorithm registration rollback.
