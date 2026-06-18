# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_psys_config_abi.h

## Purpose

This header defines the processing-system firmware configuration block.

## Important APIs, Types, and Functions

`struct ipu7_psys_config` contains debug manifest selection, timeout, compression support, logger config, watchdog config, a PSYS debug bitmask, and padding.

## Control Flow

No executable flow. A PSYS boot path would allocate/fill this config and pass its DMA address through the common boot config mechanism.

## State and Persistence Behavior

The structure is DMA-visible firmware configuration state for PSYS boot lifetime.

## Dependencies and Integration Points

It includes boot and common config ABI headers. Its fields align with firmware logging, watchdog, compression, and debug-manifest behavior.

## Risks and Edge Cases

Compression and debug flags alter firmware behavior. Packed layout and padding must remain stable.

## Test Signals

PSYS firmware boot with default and debug/compression configurations, plus boot config size and DMA sync checks.
