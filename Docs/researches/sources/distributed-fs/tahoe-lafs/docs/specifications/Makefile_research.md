## sources/distributed-fs/tahoe-lafs/docs/specifications/Makefile

Purpose: builds raster/vector derivatives for specification diagrams from SVG sources.

Important targets: default `all`, `images-png`, `images-eps`, pattern rules `%.png: %.svg` and `%.eps: %.svg`, and `clean`.

Control flow: lists SVG sources, derives PNG and EPS names, uses Inkscape to export white-background 90 DPI PNGs and EPS files, and removes generated outputs on clean.

State and dependencies: writes generated image files beside the SVGs. Depends on Inkscape command-line flags compatible with the installed version.

Risks: Inkscape CLI flags have changed across versions, so builds may fail on newer installations. Generated files are deterministic only to the extent Inkscape output is stable.
