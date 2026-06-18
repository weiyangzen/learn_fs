# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/hda_component.h

## Purpose
This header defines the shared HDA side-codec component binding interface. It is the contract between HDA codec parents and side-codec component drivers.

## Important APIs, types, and functions
`HDA_MAX_COMPONENTS` is 4 and `HDA_MAX_NAME_SIZE` is 50. `struct hda_component` stores a bound side-codec device, printable name, ACPI device, notification support and callback, and three playback hook phases. `struct hda_component_parent` stores the parent mutex, HDA codec pointer, and component array. The header declares manager APIs for ACPI notification binding, playback hook fanout, component manager init/free/bind, and has helpers `hda_component_from_index()` and `hda_component_manager_unbind()`.

## Control flow
Parent drivers initialize a manager with expected component count and match strings, bind all components when ready, call playback hook fanout during HDA PCM actions, and free/unbind the manager during codec teardown. With `CONFIG_ACPI` disabled, ACPI helper functions become no-op inline stubs.

## State and persistence
The parent struct is caller-owned and persists for the HDA codec lifetime. Component slots are filled by side-codec bind callbacks and cleared on unbind. The inline index helper bounds-checks access to the fixed component array.

## Dependencies and integration points
Dependencies include Linux ACPI, component framework, mutexes, and HDA codec types. The header is included by manager implementation and by smart-amp drivers that need to fill component slots or call playback/notification manager APIs.

## Risks and edge cases
Callers must not request more than four components. `hda_component_manager_unbind()` assumes `parent` and `cdc` are valid and takes the mutex around `component_unbind_all()`. ACPI notification stubs mean code must not depend on notification side effects when ACPI is disabled.

## Test signals
Compile with and without `CONFIG_ACPI`, test bounds behavior of `hda_component_from_index()`, verify component slot lifecycle across bind/unbind, and run multi-amp playback hook fanout through a parent HDA codec driver.
