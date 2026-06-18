# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/en-US.ts

## Purpose
This file is the English message catalog for dashboard internationalization.

## APIs, Control Flow, and State
It exports a default object mapping message IDs to English strings for resource table labels, pod/PV/PVC failure diagnostics, config editing, batch upgrade workflows, CacheGroup management, YAML display, diagnosis, warmup, and smooth-upgrade disabled messaging. There is no runtime state.

## Dependencies and Integration Points
`FormattedMessage` usages across components reference these IDs. The catalog must stay aligned with the Chinese catalog and any route/page additions.

## Risks and Test Signals
Missing keys render fallback IDs in UI. Some strings include operational guidance and must match current CSI behavior. Test locale switching, search for `FormattedMessage id=` keys missing in this file, and verify diagnostics against utility return values.
