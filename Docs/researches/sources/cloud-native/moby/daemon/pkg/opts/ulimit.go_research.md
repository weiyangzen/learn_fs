<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit.go -->
# sources/cloud-native/moby/daemon/pkg/opts/ulimit.go

## Purpose
Implements pflag/config parsing for default container ulimit settings.

## Important APIs, Types, And Functions
`UlimitOpt` wraps `map[string]*container.Ulimit`; `Set` uses `units.ParseUlimit`; `String` and `GetList` expose values. `NamedUlimitOpt` adds a config field name.

## Control Flow
Setting a value parses the `name=soft:hard` string, then stores it by ulimit name, replacing any prior entry. Listing and stringification iterate the map.

## State, Dependencies, And Integration Points
State is an in-memory map referenced from daemon config. Dependencies are Docker API container types and `docker/go-units`. Defaults are later applied to container host config/resource limits.

## Risks And Test Signals
Map iteration order is unstable; tests allow two expected string orders. Pointer-valued map entries can be mutated by callers. `ulimit_test.go` covers valid append, invalid type rejection, String, and GetList.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/opts/ulimit.go -->
