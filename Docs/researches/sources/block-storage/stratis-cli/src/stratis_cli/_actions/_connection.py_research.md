# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_actions/_connection.py

## Role

Provides the shared D-Bus connection and object lookup helper for action modules.

## Main Components

- `Bus` lazily stores a singleton `dbus.SystemBus()` in class variable `_BUS`.
- `Bus.get_bus()` initializes and returns the system bus.
- `get_object(object_path)` returns a proxy object for the Stratis service and object path.

## Dependencies

Uses `dbus` and the service name from `_actions/_constants.py`.

## Notable Behavior

The process reuses one system-bus connection for all action calls. This keeps action modules simple but means connection failures surface through D-Bus exceptions handled later in `_error_reporting.py`.
