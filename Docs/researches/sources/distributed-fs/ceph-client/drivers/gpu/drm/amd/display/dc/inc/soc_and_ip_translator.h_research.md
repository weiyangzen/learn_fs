# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/soc_and_ip_translator.h

## Purpose

`soc_and_ip_translator.h` declares a small translation boundary between DC/DML resource state and SoC/IP parameter structures. It is used where display validation needs SoC and IP capabilities in a translated form.

## Important APIs, Types, And Functions

The header is intentionally tiny. It forward-declares or includes the structures needed by the translation function and declares the translator entry point that fills SoC/IP data from DC context or resource data for DML consumers.

## Control Flow

Validation or resource setup calls the translator before DML calculations. The translator reads DC capabilities and populates the SoC/IP structures consumed by bandwidth and mode validation.

## State And Persistence Behavior

No state is stored by the header. Generated SoC/IP parameter structures are transient inputs to validation, but their values affect accepted display configurations and resource decisions.

## Dependencies And Integration Points

It integrates with DML/DML2, resource validation, ASIC capability tables, and display mode validation. Because the header is minimal, include-order and forward declaration correctness are the main source-level concern.

## Risks And Test Signals

Risks include stale translations after capability changes and mismatch between DC resource caps and DML expectations. Test signals include DML validation on multiple ASIC families, bandwidth-limit modes, high-resolution multi-display configurations, and compile coverage when DML structures change.
