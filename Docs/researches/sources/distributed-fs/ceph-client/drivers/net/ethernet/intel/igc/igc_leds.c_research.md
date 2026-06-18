# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_leds.c

## Purpose
`igc_leds.c` integrates IGC hardware LEDs with the Linux LED class and netdev trigger hardware-control API. It exposes three LEDs that can be set on/off or offloaded to link/activity indications.

## Important APIs, Types, And Functions
The public functions are `igc_led_setup()` and `igc_led_free()`. `struct igc_led_classdev` binds a `net_device`, LED class device, and LED index. Static helpers select LEDCTL masks/shifts, read/write LED mode, set brightness, validate hardware-control flags, set/get hardware-control mode, return the controlled netdev device, generate LED names, and register one LED classdev.

## Control Flow
Setup initializes `adapter->led_mutex`, allocates three LED descriptors, and registers each class device. On failure it unregisters already registered LEDs and frees memory. Brightness and hardware-control callbacks translate LED class requests into LEDCTL mode and blink bits. Register access is wrapped by runtime PM get/put and serialized by `adapter->led_mutex`. Free unregisters all three class devices and releases the allocation.

## State And Persistence
The file stores `adapter->leds` and mutates the hardware `IGC_LEDCTL` register. LED class devices use `LED_RETAIN_AT_SHUTDOWN`, so final LED state may be retained by the LED subsystem/hardware across shutdown paths. No NVM state is changed.

## Dependencies And Integration Points
It depends on Linux LED, netdev trigger, runtime PM, PCI naming, and `igc.h` for adapter state and register access. `igc_main.c` calls setup during probe and free during remove. Hardware control supports link speeds 10/100/1000/2500 and combined Rx+Tx activity.

## Risks
`igc_setup_ldev()` assigns `led_cdev->name` to a stack buffer, which is a lifetime-sensitive pattern to review against LED core behavior. Unsupported trigger combinations must return `-EOPNOTSUPP` to avoid programming ambiguous modes. Runtime PM errors from `pm_runtime_get_sync()` are not checked. Incorrect LED selection would write wrong LEDCTL bits.

## Test Signals
Signals include LED class device registration under `/sys/class/leds`, brightness on/off writes, netdev trigger offload for single link modes and combined Rx+Tx activity, rejection of unsupported flag combinations, suspend/resume behavior, probe/remove cleanup, and concurrent LED updates without register corruption.
