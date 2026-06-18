# sources/cloud-native/moby/daemon/cdi.go

## Purpose
Registers and implements Docker's CDI device driver, allowing container device requests to inject Container Device Interface devices into OCI specs and list discovered CDI devices.

## Important APIs, Types, And Functions
Defines `cdiHandler`, `RegisterCDIDriver`, `newCDIDeviceDriver`, `createCDICache`, `injectCDIDevices`, `getErrors`, and `listDevices`.

## Control Flow
Registration resolves configured spec directory symlinks, builds a CDI cache, and registers a driver named `cdi`. Cache creation errors do not fail daemon startup; instead the registered driver returns injection errors and list warnings. Injection rejects nonzero `Count` and nonempty `Options`, then passes requested device IDs to `registry.InjectDevices`. Listing emits cache warnings and `system.DeviceInfo` IDs.

## State And Persistence
State lives in the CDI cache, which watches/parses spec directories outside this file. No specs are written. Directory symlink resolution mutates the argument slice before cache creation.

## Dependencies And Integration Points
Integrates with daemon device driver registration, runtime-spec mutation, Docker config, errdefs, system device listing, and `tags.cncf.io/container-device-interface/pkg/cdi`.

## Risks And Test Signals
Startup tolerance means CDI misconfiguration appears later at request time. Directory errors except missing paths become warnings. No direct tests in this subset; integration tests should cover invalid requests, cache errors, and device injection effects.
