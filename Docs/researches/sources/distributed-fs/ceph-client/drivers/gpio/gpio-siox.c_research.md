# sources/distributed-fs/ceph-client/drivers/gpio/gpio-siox.c

## Purpose
This SIOX GPIO driver exposes a 20-line GPIO device over a SIOX cyclic I/O device: 12 input lines from received data and 8 output lines staged for the next SIOX transfer cycle. It also synthesizes nested interrupts from input level changes.

## Important APIs, Types, and Functions
`struct gpio_siox_ddata` contains the gpio chip, mutex-protected set/get data buffers, IRQ spinlock, enable/status masks, and per-input IRQ types. SIOX callbacks `gpio_siox_set_data()` and `gpio_siox_get_data()` exchange data with the bus. Gpiolib callbacks enforce fixed input/output line ranges. IRQ callbacks manage software status/type/enable bits.

## Control Flow
Probe allocates state, initializes locks, fills a sleep-capable 20-line gpio chip, configures an immutable threaded IRQ chip, and registers it. During each SIOX receive cycle, `gpio_siox_get_data()` compares new 12-bit input data against previous data, sets software IRQ status for matching level/edge triggers, updates cached input bytes, and calls `handle_nested_irq()` for enabled triggered inputs after dropping the mutex.

## State and Persistence
Outputs are staged in `setdata[0]` and only become visible to hardware in the next `set_data` cycle. Inputs are cached in `getdata[3]`. IRQ status/type/enable state is purely software. No suspend/resume hooks are present.

## Dependencies and Integration Points
The driver integrates with the SIOX bus, gpiolib, nested threaded IRQ handling, and OF module matching through the SIOX device infrastructure.

## Risks
Output `set()` does not immediately drive hardware; consumers must tolerate cycle latency. IRQs exist only for the first 12 input lines; direction callbacks reject invalid ranges. `gpio_siox_irq_set_type()` accepts arbitrary type bit combinations without validation. There is careful lock ordering between mutex and raw spinlock in receive processing.

## Test Signals
Test fixed direction boundaries at line 12, delayed output staging, input cache updates, rising/falling/high/low trigger generation, mask/unmask behavior, nested IRQ handling, and SIOX cycle concurrency with GPIO get/set calls.
