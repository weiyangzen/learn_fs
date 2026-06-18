## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_ddc.h

Purpose: small public-private header declaring AST DDC adapter creation.

Important API is `struct i2c_adapter *ast_ddc_create(struct ast_device *ast)`, with forward declarations for `ast_device` and `i2c_adapter`. There is no runtime control flow or state in the header.

Dependencies are the implementation in `ast_ddc.c` and output code that needs an I2C bus for EDID. Integration risks are minimal: prototype drift would break builds, while actual DDC behavior depends on the implementation. Test signals are compile/link success and VGA output paths obtaining an adapter for connector EDID probing.
