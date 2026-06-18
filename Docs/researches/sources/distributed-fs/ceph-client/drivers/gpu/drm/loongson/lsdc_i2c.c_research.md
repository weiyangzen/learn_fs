# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_i2c.c

Purpose: creates bit-banged DDC I2C adapters using Loongson display-controller GPIO registers.

Important APIs/types/functions: low-level GPIO set/get helpers, I2C algo callbacks, managed destroy action, and `lsdc_create_i2c_chan`.

Control flow: channel creation allocates `lsdc_i2c`, assigns SDA/SCL masks by display pipe, points to GPIO direction/data registers, fills `i2c_algo_bit_data`, initializes adapter metadata, registers the bit-bang bus, and registers DRM-managed cleanup. Set high switches the pin to input so pull-ups raise it; set low switches to output and writes zero. Reads force input and sample data.

State and persistence: each display pipe stores `dispipe->li2c`. Adapter and GPIO state persist until DRM-managed cleanup removes the adapter and frees memory.

Dependencies and integration points: used by descriptor `create_i2c` hook before output init. Output connectors use adapter as DDC. Register access is serialized with `ldev->reglock`.

Risks and test signals: invalid index leaks the allocated object because the error path returns before freeing. GPIO register semantics are chip-specific. Test EDID reads on both pipes, probe error cleanup, lock coverage under concurrent HPD/modeset, and invalid index handling.
