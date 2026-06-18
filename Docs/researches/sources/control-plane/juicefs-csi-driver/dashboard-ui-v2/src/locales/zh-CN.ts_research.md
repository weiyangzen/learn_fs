# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/zh-CN.ts

## Purpose
This file is the Simplified Chinese message catalog for the dashboard.

## APIs, Control Flow, and State
It exports a default object keyed by the same message IDs used by the UI. It covers table labels, resource states, diagnostic explanations, config editing, batch upgrade, CacheGroup, YAML, diagnosis, and smooth-upgrade disabling. It contains no executable control flow.

## Dependencies and Integration Points
The application locale provider consumes this object when Chinese is selected. Utility functions return message IDs that must exist here.

## Risks and Test Signals
Catalog drift with `en-US.ts` can leave untranslated or missing keys. One key uses `batch` while English uses `stage`, so key parity should be checked. Test all `FormattedMessage` references and language toggle rendering.
