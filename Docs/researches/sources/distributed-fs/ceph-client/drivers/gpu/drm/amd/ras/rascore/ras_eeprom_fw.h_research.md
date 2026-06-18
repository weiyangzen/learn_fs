# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom_fw.h

Purpose: this header declares the firmware EEPROM control structure and public operations that let core and UMC use MP1/SMU-managed persistent bad-page storage through an EEPROM-like interface.

Important types and APIs: `struct ras_fw_eeprom_control` tracks firmware table version, threshold mode/count, record count, max capacity, mutex, bad-channel bitmap, and update flag. Exported functions cover feature discovery, table version/count, MCA address/IPID/timestamp retrieval, timestamp setting, table erase/reset, safety-watermark checking, append/read/update operations, init/fini, storage status, GPU health, and notification sync.

Control flow and state: no active code lives here. The declarations define the integration seam used by `ras_core.c` to choose firmware storage and by `ras_umc.c` to load/save bad pages without knowing whether persistence is firmware-backed or I2C-backed.

Dependencies and integration: the header assumes `struct ras_core_context`, `struct eeprom_umc_record`, `struct ras_bank_ecc`, and `enum ras_gpu_health_status` are visible through broader `ras.h` include context. Risks are mainly API contract drift with `ras_eeprom.h`: callers expect matching semantics for count, append, read, health, and threshold operations even though firmware has different durability and indexing behavior. Test signals should compile both backends under the same caller paths and validate identical behavior for disabled retirement, record counting, channel bitmap notifications, and RMA state reporting.
