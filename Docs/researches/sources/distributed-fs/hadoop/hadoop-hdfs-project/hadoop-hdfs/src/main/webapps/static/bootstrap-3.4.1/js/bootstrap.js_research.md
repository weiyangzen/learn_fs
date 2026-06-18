# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/webapps/static/bootstrap-3.4.1/js/bootstrap.js

## Purpose

`bootstrap.js` is the readable Bootstrap v3.4.1 JavaScript bundle vendored into the HDFS web UI. It supplies jQuery plugins for transitions, alerts, buttons, carousels, collapses, dropdowns, modals, tooltips, popovers, scrollspy, tabs, and affix behavior used by Hadoop webapp pages.

## Important APIs and types

- Startup checks require jQuery >= 1.9.1 and < 4.
- `$.support.transition` and `$.fn.emulateTransitionEnd(duration)` normalize CSS transition end handling.
- Plugins are exposed as `$.fn.alert`, `button`, `carousel`, `collapse`, `dropdown`, `modal`, `tooltip`, `popover`, `scrollspy`, `tab`, and `affix`, each with `Constructor` and `noConflict()`.
- Each plugin stores state in `data('bs.<plugin>')`, exposes string-method dispatch, emits `*.bs.<plugin>` events, and has data-API bindings for `data-toggle`, `data-dismiss`, `data-slide`, `data-spy`, and related attributes.
- Tooltip/popover include an HTML sanitizer with `DefaultWhitelist`, safe URL patterns, and disallowed data attributes for sanitizer configuration.

## Control flow

The bundle is organized as independent IIFEs. Plugins initialize from direct jQuery calls or data-API events. Most visible state changes trigger cancellable `show`/`hide`/`close`/`slide` events, update classes/ARIA attributes, then complete immediately or after transition-end emulation. Data-API sections register delegated document/window handlers for alerts, carousels, collapses, dropdowns, modals, scrollspy, tabs, and affix on click/load/scroll.

Tooltip and popover share the most involved flow: initialization merges defaults, data attributes, and options; show computes placement and viewport adjustments, sanitizes configured HTML when enabled, inserts the tip, and tracks hover/focus/click state; hide detaches the tip and clears ARIA state.

## State and persistence behavior

State is in DOM classes, ARIA attributes, inline styles, event handlers, timers, and jQuery data. Modals also track body scrollbar compensation and backdrop elements. Scrollspy maintains offsets/targets and active target. Affix tracks affixed state, pinned offset, and scroll target. There is no durable persistence.

## Dependencies and integration points

The file depends on jQuery and browser DOM/CSS transition support. Hadoop pages use Bootstrap tabs, modals, popovers, buttons, dropdown-style classes, and alerts from this bundle. `explorer.js` relies on modals, popovers, and button state; `dfshealth.js`, `jn.js`, and `snn.js` rely on tab activation and alert styling.

## Risks and edge cases

- Vendored Bootstrap 3.4.1 must remain aligned with the CSS version in the webapp.
- Plugin methods often accept string dispatch; invalid method names can throw runtime errors.
- Tooltip/popover sanitizer is helpful but does not protect arbitrary application HTML outside those plugins.
- Global data-API handlers can conflict with application handlers if event namespaces or markup are changed.
- Browser layout measurements in modal, tooltip, scrollspy, and affix paths are sensitive to hidden elements, SVGs, scrolling containers, and resize timing.

## Test signals

Use upstream Bootstrap 3.4.1 JavaScript tests as baseline. Hadoop-specific smoke tests should verify tab switching, explorer delete/upload/mkdir modals, permission popovers, editable-field popovers, alert dismissal, and tooltip/popover sanitization behavior under the jQuery version shipped with the webapps.
