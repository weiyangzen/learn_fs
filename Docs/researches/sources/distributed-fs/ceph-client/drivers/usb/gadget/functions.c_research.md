# sources/distributed-fs/ceph-client/drivers/usb/gadget/functions.c

## Purpose

`functions.c` implements the libcomposite USB function-driver registry. It lets composite gadgets look up function instances by name, autoload missing function modules, allocate/free function instances, allocate/free concrete functions, and register/unregister function drivers.

## Important APIs, Types, and Functions

Exported symbols are `usb_get_function_instance()`, `usb_get_function()`, `usb_put_function_instance()`, `usb_put_function()`, `usb_function_register()`, and `usb_function_unregister()`. Internal helper `try_get_usb_function_instance()` searches `func_list` under `func_lock`, takes the provider module reference, calls `alloc_inst()`, and links the returned instance to its `usb_function_driver`.

## Control Flow

Composite gadget code calls `usb_get_function_instance("name")`. The registry first searches registered drivers. If absent, `usb_get_function_instance()` calls `request_module("usbfunc:%s", name)` and retries. Once a function instance exists, callers call `usb_get_function(fi)` to allocate a concrete `struct usb_function` from the driver's `alloc_func()` callback. Put paths call driver-provided free callbacks and drop module references.

## State and Persistence Behavior

The global `func_list` stores registered `struct usb_function_driver` entries for the lifetime of their modules. Function instances and functions are dynamic in-memory objects owned by composite gadget bind/unbind paths. No state is persisted.

## Dependencies and Integration Points

The file depends on libcomposite types, Linux module reference counting, kernel lists, and module autoload aliases. It is used by configfs gadgets and legacy precomposed gadgets throughout `drivers/usb/gadget`.

## Risks and Test Signals

Risks include module-reference leaks on allocation failures, duplicate driver names, use-after-unregister if consumers hold stale instances, and autoload failures returning the correct errno. Tests should load/unload function modules, request present and absent function names, hit duplicate registration, and exercise bind/unbind error paths in legacy gadgets that call these APIs repeatedly.
