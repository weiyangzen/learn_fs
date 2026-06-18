<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv04.c

## Purpose
This file implements support for NV04-era external TV encoders, currently probing and binding CH7006 devices over I2C and bridging them into the Nouveau DRM encoder helper model.

## Important APIs, Types, and Functions
`nv04_tv_identify` probes the configured I2C bus for supported TV encoder board info. `nv04_tv_create` constructs the DRM encoder. Helper callbacks include `nv04_tv_dpms`, `nv04_tv_prepare`, `nv04_tv_mode_set`, `nv04_tv_commit`, and `nv04_tv_destroy`. The file also defines the CH7006 board-info/platform-data table.

## Control Flow
Creation probes the DCB I2C bus, allocates a `nouveau_encoder`, initializes a TVDAC DRM encoder, records DCB output and OR, initializes the slave encoder through `nouveau_i2c_encoder_init`, creates slave resources, and attaches to the connector. Prepare powers the slave off, disables flat-panel output on the target head, unbinds the other head on dual-head chips, and binds TV routing. Mode set writes TV totals/skews/delays into the NV04 mode shadow and delegates chip-specific mode programming. DPMS updates PLL source selection bits, inhibits hsync when on, writes PRAMDAC PLL select, and delegates DPMS to the slave.

## State and Persistence Behavior
It mutates `nv04_display.mode_reg` fields such as `pllsel`, per-head CRTC `CRE_49`, `tv_setup`, and TV timing registers. The external encoder state is owned by the slave driver, while this bridge owns DRM encoder lifetime and DCB association.

## Dependencies and Integration Points
The file depends on CH7006 public parameters, Nouveau I2C encoder wrappers, DCB output entries, I2C bus probing, NV04 DFP disable/bind helpers, RAMDAC/VGA register helpers, and DRM encoder helper callbacks.

## Risks
Only probed external encoders in the static table are supported. TV PLL selection clears both CRTC TV masks before setting the active one, so multi-output assumptions are narrow. Bind/unbind sequencing touches LCD and TV setup registers and may conflict with simultaneous FP outputs. Failure after encoder init must clean both DRM and slave resources correctly.

## Test Signals
Test external CH7006 probe through DCB I2C index, TV connector resource properties, DPMS on/off PLL bits, mode set for supported timings, dual-head bind/unbind behavior, coexistence with DFP outputs, encoder destroy/unload, and connector detect delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv04.c -->
