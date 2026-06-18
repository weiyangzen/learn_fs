<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/eslint.config.cjs -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/eslint.config.cjs

## Purpose
This CommonJS flat ESLint configuration defines linting for the Vite/React/TypeScript dashboard application.

## Important APIs, Types, and Functions
It uses `defineConfig` and `globalIgnores` from `eslint/config`, `FlatCompat` from `@eslint/eslintrc`, `fixupConfigRules` from `@eslint/compat`, `@typescript-eslint/parser`, `eslint-plugin-react-refresh`, `eslint-plugin-react-hooks`, `@eslint/js`, and `globals.browser`. It extends recommended ESLint, TypeScript, and React Hooks presets, enables `react-refresh/only-export-components`, and disables `react-hooks/set-state-in-effect`.

## Control Flow, State, and Persistence
The module exports a static config array. `FlatCompat` translates legacy `extends` entries into flat config entries. The ignore block excludes `dist` and the config file itself. There is no runtime persistence; the file affects lint command behavior and editor integrations.

## Dependencies and Integration Points
It is invoked by `pnpm lint` from `package.json`. Because the application package has `"type": "module"`, the `.cjs` extension is important for `require`-style config loading.

## Risks and Test Signals
Risks include version skew between ESLint 10 flat config and compatibility wrappers, linting all JS/TS files with the TypeScript parser without project-aware type checking, and hiding hook set-state-in-effect warnings. Signals are `pnpm lint` success, expected React Refresh warnings, and no accidental linting of build output.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/eslint.config.cjs -->
