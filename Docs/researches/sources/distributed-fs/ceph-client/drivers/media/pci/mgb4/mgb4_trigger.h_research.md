# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_trigger.h

- Purpose: Declaration header for MGB4 IIO trigger lifecycle.
- Important APIs/types/functions: `mgb4_trigger_create` and `mgb4_trigger_free`.
- Control flow: Core calls create after video endpoints and free before endpoint removal.
- State and persistence: No state; lifecycle functions own an `iio_dev` returned to core.
- Dependencies and integration points: Depends on IIO types and `struct mgb4_dev` visibility from including files.
- Risks: No include guard is present, so duplicate inclusion could redeclare prototypes only; harmless but inconsistent.
- Test signals: Compile and probe/remove tests with IIO enabled.
