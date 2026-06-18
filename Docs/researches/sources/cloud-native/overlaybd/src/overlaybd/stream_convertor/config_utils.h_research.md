# sources/cloud-native/overlaybd/src/overlaybd/stream_convertor/config_utils.h

## Purpose
Provides the YAML configuration base class, accessor macros, recursive merge helper, and yaml-cpp conversion hook for stream convertor config structs.

## Important APIs and Types
`App::ConfigGroup` derives from `YAML::Node`, can load a YAML file, and includes `charfilter` for stripping hyphens. `APPCFG_PARA` and `APPCFG_CLASS` generate typed accessors/constructors. `mergeConfig` recursively overlays maps. `YAML::convert<T>` supports encoding/decoding classes derived from `ConfigGroup`.

## Control Flow
`mergeConfig` clones the left node, walks right-hand keys, recursively merges map values when keys already exist, and otherwise copies new keys. Non-map nodes are replaced by the right node.

## State and Persistence
The helper stores config as in-memory YAML nodes loaded from disk by yaml-cpp. No persistence is written.

## Dependencies and Integration Points
Depends on Photon `ENABLE_IF_BASE_OF` utility, yaml-cpp, and the config structs in `config.h`.

## Risks
Because config groups inherit from `YAML::Node`, object slicing and implicit node conversions can be subtle. `parseYAML` takes `const std::string&` but calls `std::move`, which has no useful effect and may confuse readers.

## Test Signals
Tests should cover recursive map merging, scalar replacement, defaults through generated accessors, and yaml-cpp conversion for nested config groups.
