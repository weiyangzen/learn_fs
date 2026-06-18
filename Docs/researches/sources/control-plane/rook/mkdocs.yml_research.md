# sources/control-plane/rook/mkdocs.yml

Purpose: configures the Rook documentation site build with Material for MkDocs.

Important APIs/types/functions: site metadata, `docs_dir: Documentation/`, Material theme and overrides, palette toggles, navigation/search features, plugins `search`, `exclude`, `awesome-pages`, `macros`, `minify`, `redirects`, `mike`, and markdown extensions including pymdownx features.

Control flow: MkDocs reads this config, applies plugin transforms, renders Markdown from `Documentation/`, generates redirects, minifies output, and supports version selection through `mike`.

State and persistence: generated site artifacts are build outputs; version metadata is managed by mike during deploy.

Dependencies/integration: depends on MkDocs Material, configured plugins, `.docs/overrides`, `.docs/macros`, and documentation tree.

Risks: plugin version mismatches can break builds; external logo/favicon URLs affect offline builds.

Test signals: `mkdocs build --strict` and `mike` version selector smoke testing.
