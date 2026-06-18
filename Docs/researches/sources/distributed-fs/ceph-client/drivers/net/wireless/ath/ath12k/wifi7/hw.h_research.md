# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hw.h

## Purpose

`hw.h` is the minimal public header for Wi-Fi 7 ath12k hardware initialization. It forward-declares `struct ath12k_base` and exposes `ath12k_wifi7_hw_init()`.

## Important API

`int ath12k_wifi7_hw_init(struct ath12k_base *ab);` is called after the bus-specific probe path has identified the hardware revision. It selects the matching Wi-Fi 7 hardware parameter table, installs Wi-Fi 7 mac80211 ops, initializes HAL, and returns an error for unsupported revisions.

## Control Flow And Integration

PCI probe in `wifi7/pci.c` and AHB probe in the wider Wi-Fi 7 folder include this header and call the init function after setting fields such as `ab->hw_rev`, memory mode, bus-specific ops, and window-register state. The implementation lives in `hw.c`.

## State And Persistence Behavior

The header owns no state. The declared function mutates the passed `ath12k_base` by assigning hardware params and ops and by invoking HAL initialization.

## Dependencies

The only compile-time dependency is the forward declaration of `struct ath12k_base`, keeping this header lightweight for bus drivers.

## Risks And Edge Cases

Because this header hides the full `ath12k_base` definition, callers must include the right core headers in their own C files before dereferencing `ab`. The main behavioral risk is caller ordering: `ab->hw_rev` must be valid before calling `ath12k_wifi7_hw_init()`.

## Test Signals

Build coverage should confirm all bus drivers see the prototype. Probe tests should verify PCI/AHB paths call the function after hardware revision selection and handle nonzero returns.
