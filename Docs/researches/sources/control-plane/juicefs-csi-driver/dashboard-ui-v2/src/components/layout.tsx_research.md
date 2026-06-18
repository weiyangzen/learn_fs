<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/layout.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/layout.tsx

## Purpose
`layout.tsx` defines the dashboard shell: fixed header, side navigation, localization provider, Ant Design locale/theme providers, and content area.

## Important APIs, Types, and Functions
It defines menu `items` for resource and tool navigation, then exports `Layout`. The component uses `useLocation`, `useVersion`, `IntlProvider`, nested `ConfigProvider`s, Ant Design `Layout`, `Menu`, `Button`, `Tooltip`, and locale dictionaries `en-US`/`zh-CN`.

## Control Flow, State, and Persistence
Locale is initialized from `window.localStorage`, defaults to `zh`, and is persisted whenever it changes. Menu selection derives from the first URL segment, with `/` treated as `/pods`. Header buttons show driver version, open docs/GitHub in new tabs, and toggle locale.

## Dependencies and Integration Points
It wraps all routed pages from `App.tsx`. It depends on browser localStorage/window, React Intl message IDs used by child components, Ant Design locale packages, icon components, and the backend version endpoint.

## Risks and Test Signals
Risks include client-only browser APIs, selected key mismatch for `/jobs` because the menu key is `/upgrade`, fixed layout responsiveness issues, and no validation of stored locale values. Signals are locale persistence tests, route/menu selection tests, mobile layout checks, and version display fallback.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/layout.tsx -->
