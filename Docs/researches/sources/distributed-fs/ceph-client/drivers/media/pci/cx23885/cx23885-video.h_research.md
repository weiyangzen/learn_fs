# Research: sources/distributed-fs/ceph-client/drivers/media/pci/cx23885/cx23885-video.h

Purpose: Small internal header exposing Flatiron audio ADC register helpers used outside `cx23885-video.c`.

Important APIs/types/functions: declares `cx23885_flatiron_write(struct cx23885_dev *dev, u8 reg, u8 data)` and `cx23885_flatiron_read(struct cx23885_dev *dev, u8 reg)`.

Control flow: video code implements these helpers for I2C access to the Flatiron device at address `0x98 >> 1`; other cx23885 modules can include this header if they need direct Flatiron access.

State and persistence: no state. The helpers access live Flatiron hardware registers.

Dependencies/integration: guarded by `_CX23885_VIDEO_H_`; assumes `struct cx23885_dev` and fixed-width integer types are in scope.

Risks: direct register access bypasses higher-level audio routing policy and can affect active capture. Header does not include dependencies itself.

Test signals: compile coverage and successful audio mux behavior on boards using Flatiron LR1/LR2 selection.
