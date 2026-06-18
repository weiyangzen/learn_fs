<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format.go -->
# sources/cloud-native/containerd/core/mount/manager/format.go

Purpose: implements the `format` mount transformer used by the mount manager to rewrite mount source, target, and option strings from templates that refer to previously activated mounts.

Important APIs/types/functions: `mountFormatter.Transform` implements `mount.Transformer`; `formatString` returns a closure only when the string contains `{{`; template funcs are `source`, `target`, `mount`, and `overlay`. `overlay(start,end)` expands active mount points in forward or reverse order joined by `:`, matching overlayfs lowerdir syntax.

Control flow: `Transform` checks `Source`, `Target`, and each option independently. It avoids allocating a replacement options slice until the first option actually changes, then copies and patches by index. `formatString` parses a Go `text/template` at execution time and bounds-checks indexes/ranges against the active mount slice.

State and persistence: no persistent state. The transform returns a modified copy of the input `mount.Mount`; only the options slice may be copied when needed.

Dependencies and integration points: used by `manager.go` in the built-in transform chain for mount types like `format/overlay`; consumes `mount.ActiveMount` values produced by earlier manager-mounted entries.

Risks: template parsing on each transform is heavier than a purpose-built formatter; error messages expose index/range details and stop activation; all template functions trust active mount order. Unescaped template syntax in otherwise literal options will be interpreted.

Test signals: `format_test.go` covers no-op formatting, source/target substitution, overlay expansion, reverse ranges, single-range expansion, and options-copy behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format.go -->
