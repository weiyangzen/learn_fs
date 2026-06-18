<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.h

## Purpose

`sun4i_tcon_dclk.h` declares the TCON channel 0 dot-clock creation and destruction functions.

## Important APIs, Types, And Functions

It exposes `sun4i_dclk_create(struct device *dev, struct sun4i_tcon *tcon)` and `sun4i_dclk_free(struct sun4i_tcon *tcon)`.

## Control Flow

The header has no executable flow. TCON bind calls create after regmap/clock setup, and bind error/unbind paths call free when channel 0 exists.

## State And Persistence Behavior

No state is stored in the header. The implementation stores the registered clock in `tcon->dclk` and manipulates TCON hardware registers.

## Dependencies And Integration Points

It forward-declares `struct sun4i_tcon` and relies on `struct device` from consumers. It links TCON lifecycle code with the common-clock provider implementation.

## Risks And Test Signals

Risks are limited to lifecycle/prototype drift. Build with TCON channel 0 support and runtime create/free during probe failure and normal remove are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tcon_dclk.h -->
