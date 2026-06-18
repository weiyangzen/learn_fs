# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.h

Purpose: conditional interface for AIC94xx debug dump helpers.

Important APIs/types/functions: declares `asd_dump_seq_state()` and `asd_dump_frame_rcvd()` when `ASD_DEBUG` is compiled. Otherwise provides static inline no-op versions with the same signatures.

Control flow: no runtime control beyond compile-time selection. Callers can invoke dump helpers unconditionally without wrapping their own `#ifdef ASD_DEBUG`.

State and persistence: no state. Debug builds emit kernel logs; non-debug builds do nothing.

Dependencies and integration: requires visible `struct asd_ha_struct`, `struct asd_phy`, and `struct done_list_struct` declarations from surrounding headers. Used by hardware interrupt/error paths.

Risks and test signals: signatures must remain aligned with `aic94xx_dump.c` and call sites. Build tests with `CONFIG_AIC94XX_DEBUG=y` and disabled are the core signal.
