# sources/cloud-native/ostree/docs/_config.yml

Purpose: Jekyll site configuration for publishing OSTree documentation under `https://ostreedev.github.io/ostree`.

Important APIs/types: Jekyll keys `title`, `description`, `baseurl`, `url`, `permalink`, `markdown`, `kramdown`, `exclude`, `include`, `remote_theme`, `plugins`, `color_scheme`, `aux_links`, footer and edit-link metadata, and `compress_html`.

Control flow: declarative. The site excludes source README/bundler/prep/vendor files, explicitly includes generated `reference` and `man` directories, uses `just-the-docs` remote theme, and enables GitHub edit links pointing at `docs` on `main`.

State and persistence: no application state; controls static site generation. Generated API and man documentation must be copied into `docs/reference` and `docs/man` before Jekyll runs.

Dependencies and integration: integrates `docs/prep-docs.sh`, GitHub Pages/Jekyll, kramdown, just-the-docs, generated gtk-doc HTML, and generated man HTML.

Risks and test signals: risks include remote theme version drift, missing generated include directories, GitHub Pages plugin constraints, and baseurl mismatches. Signals are successful local/CI Jekyll builds and working reference/man links.
