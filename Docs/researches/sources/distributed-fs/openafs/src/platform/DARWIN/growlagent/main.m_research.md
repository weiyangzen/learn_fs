# sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/main.m

## Purpose
Implements a Darwin Growl notification agent for OpenAFS. It listens on UDP port `2106` for Venus Monitor messages, converts message prefixes such as `fetch$`, `store$`, and `warn$` into Growl notification metadata, and posts notifications either through `GrowlApplicationBridgePathway` or `NSDistributedNotificationCenter`.

## Important APIs, Types, And Functions
Key functions are `getPath`, `MyTransmit`, `BuildNotificationInfo`, `MySocketReadCallBack`, `readFile`, and `main`. The file uses CoreFoundation types (`CFNotificationCenterRef`, `CFDictionaryRef`, `CFDataRef`, `CFSocketRef`), Objective-C `NSConnection`/`NSDistantObject`, and Growl constants/protocols from `GrowlDefines.h` and `GrowlPathway.h`. `GrowlCBContext` carries the distributed notification center, registration dictionary, and icon data into the socket callback.

## Control Flow
`main` loads `Andy.icns`, constructs a Growl registration dictionary for the single `OpenAFS Venus Monitor` notification class, creates an IPv4 UDP socket bound to `INADDR_ANY:2106`, registers `MySocketReadCallBack` as a CoreFoundation read callback, adds the socket source to the current run loop, and blocks in `CFRunLoopRun`. On datagram receipt, the callback null-terminates the received buffer and calls `BuildNotificationInfo`, which chooses notification text, priority, and identifier based on the prefix. `MyTransmit` first tries direct Growl IPC and falls back to distributed notifications.

## State And Persistence
Runtime state is held in CoreFoundation objects, the UDP socket, and the callback context. There is no disk persistence beyond reading the bundled icon. Notifications are transient, with generated UUID click context values.

## Dependencies And Integration Points
Integrates OpenAFS cache-manager monitor output with macOS Growl. It depends on Foundation/AppKit/CoreFoundation, Mach-O executable path APIs, BSD sockets, and legacy Growl IPC/distributed notification contracts.

## Risks And Test Signals
Risks include legacy Growl availability, unchecked `recvfrom` return handling when `result <= 0`, possible CF object leaks for created description strings and UUIDs, and binding conflicts on UDP port 2106. Test signals are successful socket bind, correct notification registration, messages for all known prefixes, fallback behavior when Growl IPC is unavailable, and run-loop cleanup on termination.
