# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.h

## Purpose
Defines the Matrox software I2C adapter wrapper used by Maven and related Matrox output code.

## Important APIs, Types, and Functions
- `struct i2c_bit_adapter` embeds an `i2c_adapter`, initialization flag, `i2c_algo_bit_data`, owning `matrox_fb_info *`, and bit masks for data/clock GPIO lines.

## Control Flow
The header is not executable, but `matroxfb_maven.c` uses `container_of(clnt->adapter, struct i2c_bit_adapter, adapter)` to recover the Matrox framebuffer instance for an I2C client.

## State and Persistence
The adapter tracks whether it has been initialized, the owning Matrox card, and the bit masks used by the bit-banged bus. Lifetime is controlled by the Matrox base/I2C setup code outside this file.

## Dependencies and Integration Points
Includes Linux ioctl and I2C headers, `i2c-algo-bit`, and `matroxfb_base.h`. It is an integration contract between Matrox framebuffer state and Linux I2C client drivers such as Maven.

## Risks
Because clients recover `matrox_fb_info` through this exact embedding, layout and adapter ownership must remain consistent. Misconfigured masks or initialization state will break downstream I2C devices.

## Test Signals
Build tests should cover I2C-enabled Matrox configurations. Runtime signals are I2C adapter registration, successful Maven client probe, and correct recovery of `minfo` from the adapter.
