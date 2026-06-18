# sources/distributed-fs/ceph-client/drivers/comedi/comedi_pcmcia.c

## Purpose

This file is the bus glue between the COMEDI core and Linux PCMCIA drivers. It lets a low-level COMEDI driver recover its `struct pcmcia_device`, enable and disable PCMCIA resources, auto-create a COMEDI device during PCMCIA probe, tear it down during remove, and register/unregister the COMEDI and PCMCIA driver halves as a pair.

## Important APIs, types, and functions

The exported APIs are `comedi_to_pcmcia_dev()`, `comedi_pcmcia_enable()`, `comedi_pcmcia_disable()`, `comedi_pcmcia_auto_config()`, `comedi_pcmcia_auto_unconfig()`, `comedi_pcmcia_driver_register()`, and `comedi_pcmcia_driver_unregister()`. They operate on `struct comedi_device`, `struct pcmcia_device`, `struct comedi_driver`, and `struct pcmcia_driver`. The private `comedi_pcmcia_conf_check()` is the default `pcmcia_loop_config()` callback and rejects configuration index 0 before requesting I/O windows.

## Control Flow

A PCMCIA low-level driver normally calls the module helper macro that expands to paired registration. Registration first inserts the COMEDI driver with `comedi_driver_register()`, then calls `pcmcia_register_driver()`, rolling back COMEDI registration if PCMCIA registration fails. During PCMCIA probe, `comedi_pcmcia_auto_config()` calls `comedi_auto_config(&link->dev, driver, 0)`, so the COMEDI core allocates the device and invokes the driver's `auto_attach`. The `auto_attach` path may call `comedi_pcmcia_enable()`, which loops through socket configurations, requests I/O resources through the supplied or default callback, and activates the card with `pcmcia_enable_device()`. Removal calls `comedi_pcmcia_auto_unconfig()`, which delegates to `comedi_auto_unconfig()`.

## State and Persistence

No durable state is stored here. Runtime state is the reference from `dev->hw_dev` to the embedded PCMCIA device, PCMCIA resource allocation state inside the PCMCIA core, and paired driver registration in kernel lists. `comedi_pcmcia_disable()` is the cleanup companion for requested PCMCIA resources and is expected after failed enable paths.

## Dependencies and Integration Points

The file depends on `linux/comedi/comedi_pcmcia.h`, the PCMCIA core, and the COMEDI auto-configuration and driver-registration APIs. It is used by PCMCIA COMEDI low-level drivers listed in the drivers Makefile, and its exported symbols are GPL-only.

## Risks

The main risk is ordering: a failed `pcmcia_register_driver()` must unregister the COMEDI driver, and a failed `comedi_pcmcia_enable()` caller must still disable/release PCMCIA resources. `comedi_to_pcmcia_dev()` assumes `dev->hw_dev` really points to a `struct device` embedded in a `struct pcmcia_device`; using it with the wrong bus device is type-unsafe after the NULL check.

## Test Signals

Useful signals are successful module load/unload, a PCMCIA COMEDI card probing through `comedi_auto_config()`, valid I/O regions after `pcmcia_loop_config()`, correct cleanup on probe failure, and no stale COMEDI devices after PCMCIA remove or user-triggered COMEDI unconfiguration.
