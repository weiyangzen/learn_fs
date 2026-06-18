# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-yaml-page.tsx

## Purpose
`ConfigYamlPage` is the raw YAML editor tab for CSI driver configuration.

## APIs, Control Flow, and State
It receives YAML text, edit flag, and setters from `ConfigDetail`. It renders a Monaco YAML editor with read-only mode when not editing. On change, non-empty values update parent config data, mark the config updated, and clear errors.

## Dependencies and Integration Points
It is one of the two tabs in `ConfigDetail`, sharing state with the structured table editor and save confirmation flow.

## Risks and Test Signals
Empty editor contents do not propagate because `if (v)` skips empty strings. Syntax validation is deferred to save or table parsing. Test read-only cursor behavior, empty YAML edits, invalid YAML, and switching between YAML and table tabs.
