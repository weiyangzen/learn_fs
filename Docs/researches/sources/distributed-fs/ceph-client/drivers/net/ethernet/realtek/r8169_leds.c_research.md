# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/r8169_leds.c

Purpose: Provides optional LED class integration for Realtek r8169-family NIC LEDs using the kernel netdev LED trigger.

Important APIs and types: `struct r8169_led_classdev` wraps `struct led_classdev`, net_device pointer, and LED index. Public functions initialize RTL8168 or RTL8125 LED arrays and remove them. Hardware-control callbacks implement trigger validation, set, get, and device lookup for both RTL8168 and RTL8125 families.

Control flow: Initialization allocates an array with a sentinel, fills each LED classdev with a generated name from `r8169_get_led_name()`, sets `hw_control_trigger` to `netdev`, retains LED state at shutdown, installs callbacks, and registers with the net_device parent. Validation rejects half/full-duplex trigger flags and requires RX/TX activity flags to be both set or both clear. Set callbacks translate netdev trigger flags to chip-specific LED mode bits. Get callbacks read current hardware mode and translate bits back to trigger flags; RTL8168 also disables unsupported OPTION2 mode if observed. Removal iterates until the sentinel `ndev` is null, unregisters LEDs, and frees memory.

State and persistence: LED state is represented by chip LED mode registers accessed through r8169 main callbacks. Allocated LED classdev arrays persist while the net_device is alive. `LED_RETAIN_AT_SHUTDOWN` asks LED core to preserve state.

Dependencies and integration: Depends on `CONFIG_R8169_LEDS`, LED class, netdev LED trigger constants, and r8169 hardware helper callbacks for mode read/write.

Risks and test signals: Risks include ignored registration failures leaving partially registered arrays, stack-allocated LED name buffers assigned to `led_cdev->name`, unsupported trigger combinations, and family-specific bit mismatches. Tests should cover init/remove, trigger set/get for each supported speed/activity combination, unsupported duplex flags, OPTION2 clearing, partial registration failures, and R8169 builds without LED support.
