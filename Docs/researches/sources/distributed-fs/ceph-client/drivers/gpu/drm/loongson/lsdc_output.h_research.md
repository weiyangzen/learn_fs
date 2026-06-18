# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_output.h

Purpose: declares chip-specific output initialization hooks for Loongson display pipes.

Important APIs/types/functions: `ls7a1000_output_init` and `ls7a2000_output_init`.

Control flow: core modeset setup calls the descriptor's `output_init` for each pipe after I2C creation.

State and persistence: no state in header; implementations initialize `lsdc_output` encoder/connector objects embedded in display pipes.

Dependencies and integration points: includes `lsdc_drv.h` and is part of `lsdc_kms_funcs`.

Risks and test signals: prototype must match descriptor function pointer. Test output init on both chips with and without DDC.
