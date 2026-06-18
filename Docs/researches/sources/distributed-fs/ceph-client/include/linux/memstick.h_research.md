<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memstick.h -->
# sources/distributed-fs/ceph-client/include/linux/memstick.h

## Purpose
This header defines the Sony MemoryStick core protocol structures, command/TPC constants, host/card/driver abstractions, request format, and bus registration APIs.

## Important APIs, types, and functions
Packed hardware register structures include status, ID, parameter, extra data, legacy register map, PRO parameter/IO registers, and register address selection. Enums define TPC transfer codes and MemoryStick/MemoryStick PRO commands. `struct memstick_device_id` describes media matching. `struct memstick_request` carries TPC, direction/card-interrupt/long-data flags, interrupt status, error, and either scatterlist or inline data. `struct memstick_dev`, `struct memstick_host`, and `struct memstick_driver` model card, host controller, and media driver callbacks. APIs cover driver registration, host allocation/add/remove/free, change detection, suspend/resume, request initialization, next/new request scheduling, RW address setup, and drvdata/private helpers.

## Control flow
Host drivers allocate and add a host, detect media changes, and service pending requests via their `request` callback. Media drivers bind by ID, provide request-generation callbacks, and use `memstick_new_req()`/`memstick_next_req()` to drive command sequences. The core handles card interrupts, retries, completion, power/interface parameters, and suspend/resume coordination.

## State and persistence
Runtime state includes host lock, capabilities, current card, retry count, removal flag, media checker work, current request, completion, register-address layout, and driver callbacks. Card flash contents persist on media; bus/core state does not.

## Dependencies and integration points
It depends on workqueues, scatterlists, completions, mutexes, device model, and PM messages. It integrates MemoryStick host controller drivers with storage or IO media drivers.

## Risks and test signals
Risks include packed-structure endian/layout assumptions, inline data length limits, request callback races during removal, retry handling, card interrupt expectations, and suspend while requests are active. Test legacy and PRO cards, storage and IO categories, host capability negotiation, request SG and inline paths, media removal, retries/errors, suspend/resume, and 4/8-bit interface switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memstick.h -->
