# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_dcc.c

## Purpose
`hvc_dcc.c` adapts ARM Debug Communications Channel access to the HVC core. It provides an early console named `dcc`, direct `hv_ops` get/put methods, and optional SMP serialization through CPU0-backed FIFOs and workqueues.

## Important APIs, Types, and Functions
The backend operations are `hvc_dcc0_get_chars()` and `hvc_dcc0_put_chars()`, backed by raw `hvc_dcc_get_chars()` and `hvc_dcc_put_chars()`. `hvc_dcc_check()` probes DCC availability by writing a test newline and waiting for the TX status bit to clear. Early console setup uses `dcc_early_console_setup()` and `dcc_early_write()`. Runtime init occurs in `hvc_dcc_console_init()` and `hvc_dcc_init()`.

When `CONFIG_HVC_DCC_SERIALIZE_SMP` is enabled, `dcc_lock`, `inbuf`, `outbuf`, `dcc_put_work()`, and `dcc_get_work()` serialize DCC access on CPU0.

## Control Flow
Early console setup waits for the DCC transmitter to become available and assigns the console write callback. Console init probes DCC and calls `hvc_instantiate(0, 0, &hvc_dcc_get_put_ops)`. Device init probes again and calls `hvc_alloc(0, 0, ..., 128)`. Reads poll the DCC RX status bit until no character is available. Writes busy-wait on the TX status bit for each byte.

## State and Persistence Behavior
The driver uses global KFIFOs for serialized SMP input/output and a static `dcc_core0_available` probe result. There is no persistent state outside DCC hardware state.

## Dependencies and Integration Points
It depends on `asm/dcc.h`, CPU hotplug/SMP helpers, kfifo, earlycon, uart console helpers, and HVC core APIs. In serialized mode it disables CPU hotplug in `hvc_dcc_init()` and warns loudly that the kernel is a debug build.

## Risks and Edge Cases
DCC put paths busy-wait, so unavailable or slow debug hardware can stall console output. Serialized SMP mode relies on CPU0 staying online and uses queued work to avoid multi-core DCC corruption. The DCC availability probe writes a newline, which is observable on the debug channel.

## Test Signals
Signals include early `earlycon=dcc` output, successful `hvc0` allocation, no hangs in `hvc_dcc_check()`, input availability through DCC RX, serialized writes from nonzero CPUs, and expected warning output when SMP serialization is configured.
