# sources/distributed-fs/ceph-client/drivers/mfd/ucb1x00-assabet.c

## Purpose
`ucb1x00-assabet.c` is a small Assabet board-specific UCB1x00 child driver. It demonstrates board integration by exposing three ADC readings as device attributes and registering a polled `gpio-keys` platform device backed by the first six UCB1x00 GPIOs.

## Important APIs, Types, And Functions
The macro `UCB1X00_ATTR()` generates read-only sysfs show functions and `DEVICE_ATTR_RO()` instances for `vbatt`, `vcharger`, and `batt_temp`. The UCB child callbacks are `ucb1x00_assabet_add()` and `ucb1x00_assabet_remove()`, wired into `struct ucb1x00_driver ucb1x00_assabet_driver`. Module init/exit call `ucb1x00_register_driver()` and `ucb1x00_unregister_driver()`.

## Control Flow
When the UCB core registers this child, `ucb1x00_assabet_add()` clears static button and key metadata, maps six buttons to `BTN_0` through `BTN_5`, assigns GPIO numbers from `ucb->gpio.base`, sets a 50 ms poll interval, and registers a `gpio-keys` platform device beneath the UCB device. It then creates the three ADC sysfs files and stores the platform device pointer in `dev->priv`. Each sysfs read enables the ADC, performs one `ucb1x00_adc_read()` on the chosen channel with `UCB_NOSYNC`, disables the ADC, and prints the raw value. Remove unregisters the gpio-keys device if valid and removes the sysfs files.

## State, Persistence, And Dependencies
The only local state is the static `buttons[6]` array and the child-private platform device pointer. Persistent behavior is external: sysfs files remain while the child is attached, and the gpio-keys platform device remains registered until removal. Dependencies include the UCB core ADC/GPIO APIs, Linux platform device creation, gpio-keys platform data, input key codes, and the UCB core's ability to provide a valid gpiolib base.

## Integration Points
This driver is loaded through the UCB1x00 pseudo-driver registry rather than a normal bus match table. It assumes the parent UCB device has GPIOs registered with a stable base and an ADC path available. The gpio-keys child integrates with the input subsystem through the generic `gpio-keys` driver, while the ADC attributes integrate through the UCB class device.

## Risks
`platform_device_register_data()` errors are stored but do not make add fail, and sysfs creation return values are ignored; partial setup can therefore appear successful. GPIO numbers are computed from `ucb->gpio.base` without checking for `-1`, so boards without gpiolib support can register invalid keys. The static `buttons[]` array means multiple UCB instances would share mutable button metadata. Sysfs reads are raw ADC values with no scaling, calibration, or locking beyond the UCB ADC mutex. Removal checks only `IS_ERR(pdev)`, not `NULL`, but add normally stores the returned pointer.

## Test Signals
Validation should load the driver after UCB core probe, confirm six gpio-keys inputs appear with expected GPIOs and 50 ms polling, and read `vbatt`, `vcharger`, and `batt_temp` while observing ADC enable/read/disable behavior. Negative tests should cover missing gpiolib base, platform-device registration failure, sysfs creation failure, and unload ordering with the parent UCB device.
